describe('template spec', () => {

    beforeEach(() => {
        cy.fixture('user').then(user => {
            cy.register_user(user.username, user.password);
            cy.login_user(user.username, user.password);
        });
    });

    it('Edit Article Test', () => {
        cy.fixture('article').then(article => {

            cy.visit('http://127.0.0.1:8000/user_app/create_article/');

            cy.get('#id_title').type(article.title);
            cy.get('#id_tags').type(article.tags);

            cy.get('#id_form-0-title').type(article.steps[0].title);
            cy.get('#id_form-0-description1').type(article.steps[0].description1);
            cy.get('#id_form-0-description2').type(article.steps[0].description2);

            cy.get('#add-step-button').click();

            cy.get('#id_form-1-title').type(article.steps[1].title);
            cy.get('#id_form-1-description1').type(article.steps[1].description1);
            cy.get('#id_form-1-description2').type(article.steps[1].description2);

            cy.get('button[type="submit"]').click();

            cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

            cy.get('.card-body').should('contain', article.title);
            cy.get('.card-body').should('contain', 'Steps: 2');
            cy.fixture('user').then(user => {
                cy.get('.card-body').should('contain', user.username);
            });
            cy.get('.card-body').should('contain', '\n' +
                '                    Tags: \n' +
                '                    #tag2 \n' +
                '                \n' +
                '                    #tag1 \n' +
                '                \n' +
                '                    #tagtest\n' +
                '                \n' +
                '                ');
        });

        cy.get('button[name="view_article"]').click();

        cy.get('button[name="edit_article"]').click();

        cy.fixture('article').then(article => {
            cy.get('#id_title').type(article.title + ' edited');
            cy.get('#id_tags').clear().type('tagedit');

            cy.get('#id_form-0-title').clear().type(article.steps[0].title + ' edited');
            cy.get('#id_form-0-description1').clear().type(article.steps[0].description1 + ' edited');
            cy.get('#id_form-0-description2').clear().type(article.steps[0].description2 + ' edited');

            cy.get('#id_form-1-title').clear().type(article.steps[1].title + ' edited');
            cy.get('#id_form-1-description1').clear().type(article.steps[1].description1 + ' edited');
            cy.get('#id_form-1-description2').clear().type(article.steps[1].description2 + ' edited');

            cy.get('#add-step-button').click();

            cy.get('#id_form-2-title').clear().type('New ' + article.steps[2].title);
            cy.get('#id_form-2-description1').clear().type('New ' + article.steps[2].description1);
            cy.get('#id_form-2-description2').clear().type('New ' + article.steps[2].description2);

            cy.get('button[type="submit"]').click();

            cy.visit('http://127.0.0.1:8000/user_app/user_panel/');

            cy.get('.card-body').should('contain', article.title + ' edited');
            cy.fixture('user').then(user => {
                cy.get('.card-body').should('contain', user.username);
            });
            cy.get('.card-body').should('contain', 'Steps: 3');
            cy.get('.card-body').should('contain', '\n' +
                '                    Tags: \n' +
                '                    #tagedit\n' +
                '                \n' +
                '                ');

        });

    });

    afterEach(() => {
        cy.visit('http://127.0.0.1:8000/registration/logout');
        cy.fixture('user').then(user => {
            cy.cleanup_user(user.username);
        });
    });

});
